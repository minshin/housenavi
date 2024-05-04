//
//  LoginView.swift
//  housenavi
//
//  Created by hiroshi on 2024/05/04.
//

import SwiftUI
import Firebase

struct AuthView: View {
    @State private var email: String = ""
    @State private var password: String = ""
    @State private var isUserLoggedIn: Bool = false

    var body: some View {
        VStack {
            if isUserLoggedIn {
                Text("欢迎回来!")
            } else {
                TextField("电子邮件", text: $email)
                SecureField("密码", text: $password)
                Button("注册") {
                    registerUser()
                }
                Button("登录") {
                    loginUser()
                }
            }
        }
        .padding()
    }
    
    func registerUser() {
        Auth.auth().createUser(withEmail: email, password: password) { authResult, error in
            if let error = error {
                print("注册失败: \(error.localizedDescription)")
            } else {
                isUserLoggedIn = true
                print("注册成功")
            }
        }
    }
    
    func loginUser() {
        Auth.auth().signIn(withEmail: email, password: password) { authResult, error in
            if let error = error {
                print("登录失败: \(error.localizedDescription)")
            } else {
                isUserLoggedIn = true
                print("登录成功")
            }
        }
    }
}

struct AuthView_Previews: PreviewProvider {
    static var previews: some View {
        AuthView()
    }
}

